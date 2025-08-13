# -*- coding: utf-8 -*-
"""
확장된 시작 아이템 시스템
직업별로 적합한 장비와 소비 아이템을 제공
"""

import random
from typing import Dict, List, Tuple
from enum import Enum

class ItemGrade(Enum):
    """아이템 등급"""
    NORMAL = "일반"
    RARE = "고급"

class ItemType(Enum):
    """아이템 타입"""
    WEAPON = "무기"
    ARMOR = "방어구"
    ACCESSORY = "장신구"
    CONSUMABLE = "소비품"

class EnhancedStartingItems:
    """확장된 시작 아이템 관리 클래스"""
    
    def __init__(self):
        self.item_database = self._init_item_database()
        self.class_preferences = self._init_class_preferences()
    
    def _init_item_database(self) -> Dict[str, Dict[str, List[Dict]]]:
        """아이템 데이터베이스 초기화"""
        return {
            "무기": {
                "일반": [
                    {"name": "철검", "attack": 15, "durability": 100, "classes": []},
                    {"name": "강철 도끼", "attack": 18, "durability": 90, "classes": []},
                    {"name": "단검", "attack": 12, "durability": 80, "classes": []},
                    {"name": "활", "attack": 14, "durability": 85, "classes": []},
                    {"name": "마법 지팡이", "attack": 10, "magic_attack": 20, "durability": 70, "classes": []},
                    {"name": "성스러운 메이스", "attack": 16, "durability": 95, "classes": []},
                     {"name": "암흑검", "attack": 17, "durability": 85, "classes": []},
                     {"name": "수도승 장갑", "attack": 13, "durability": 120, "classes": []},
                     {"name": "하프", "attack": 8, "magic_attack": 15, "durability": 60, "classes": []},
                     {"name": "용검", "attack": 19, "durability": 110, "classes": []},
                     {"name": "레이저 건", "attack": 16, "durability": 75, "classes": []},
                     {"name": "해적검", "attack": 15, "durability": 80, "classes": []},
                     {"name": "사무라이도", "attack": 20, "durability": 100, "classes": []},
                     {"name": "자연의 지팡이", "attack": 11, "magic_attack": 18, "durability": 90, "classes": []},
                     {"name": "철학서", "attack": 9, "magic_attack": 22, "durability": 50, "classes": []},
                     {"name": "기사창", "attack": 17, "durability": 105, "classes": []},
                     {"name": "검투사 검", "attack": 16, "durability": 95, "classes": []}
                ],
                "고급": [
                    {"name": "미스릴 검", "attack": 25, "durability": 150, "special": "크리티컬 +5%", "classes": []},
                    {"name": "화염 도끼", "attack": 28, "durability": 140, "special": "화염 피해 +10", "classes": []},
                    {"name": "독침 단검", "attack": 22, "durability": 120, "special": "독 효과", "classes": []},
                    {"name": "엘븐 활", "attack": 24, "durability": 130, "special": "명중률 +10%", "classes": []},
                    {"name": "대마법사 지팡이", "attack": 15, "magic_attack": 35, "durability": 110, "special": "마나 회복 +2", "classes": []},
                    {"name": "성스러운 검", "attack": 26, "durability": 160, "special": "언데드 특효", "classes": []},
                    {"name": "저주받은 검", "attack": 30, "durability": 120, "special": "생명력 흡수", "classes": []},
                    {"name": "용의 발톱", "attack": 23, "durability": 180, "special": "기 회복 +1", "classes": []},
                    {"name": "마법 하프", "attack": 12, "magic_attack": 25, "durability": 100, "special": "파티 버프 강화", "classes": []},
                    {"name": "드래곤 소드", "attack": 32, "durability": 170, "special": "화염 저항 +20%", "classes": []},
                    {"name": "플라즈마 캐논", "attack": 28, "durability": 110, "special": "관통 공격", "classes": []},
                    {"name": "영혼 지팡이", "attack": 14, "magic_attack": 30, "durability": 130, "special": "영혼 피해 +15", "classes": []}
                ]
            },
            "방어구": {
                "일반": [
                    {"name": "가죽 갑옷", "defense": 8, "durability": 80, "classes": []},
                    {"name": "철 갑옷", "defense": 15, "durability": 120, "classes": []},
                    {"name": "마법사 로브", "defense": 5, "magic_defense": 12, "durability": 60, "classes": []},
                    {"name": "성직자 의복", "defense": 10, "magic_defense": 8, "durability": 90, "classes": []},
                    {"name": "수도복", "defense": 12, "durability": 100, "classes": []},
                    {"name": "음유시인 의상", "defense": 7, "durability": 70, "classes": []},
                    {"name": "용린 갑옷", "defense": 18, "durability": 140, "classes": []},
                    {"name": "검성 도복", "defense": 13, "durability": 110, "classes": []},
                    {"name": "기계 슈트", "defense": 16, "durability": 100, "classes": []},
                    {"name": "자연의 갑옷", "defense": 11, "magic_defense": 9, "durability": 85, "classes": []},
                    {"name": "무당 의복", "defense": 9, "magic_defense": 11, "durability": 75, "classes": []}
                ],
                "고급": [
                    {"name": "미스릴 갑옷", "defense": 25, "durability": 180, "special": "마법 저항 +10%", "classes": []},
                    {"name": "그림자 갑옷", "defense": 18, "durability": 150, "special": "은신 +15%", "classes": []},
                    {"name": "대마법사 로브", "defense": 12, "magic_defense": 22, "durability": 120, "special": "마나 최대치 +20", "classes": []},
                    {"name": "성스러운 갑옷", "defense": 28, "durability": 200, "special": "언데드 저항", "classes": []},
                    {"name": "암흑 갑옷", "defense": 22, "durability": 160, "special": "생명력 흡수 +5%", "classes": []},
                    {"name": "용의 비늘 갑옷", "defense": 30, "durability": 220, "special": "화염 면역", "classes": []},
                    {"name": "강화 기계 슈트", "defense": 26, "durability": 140, "special": "전기 저항 +50%", "classes": []}
                ]
            },
            "장신구": {
                "일반": [
                    {"name": "힘의 반지", "attack": 3, "durability": 200, "classes": []},
                    {"name": "민첩의 목걸이", "speed": 5, "durability": 180, "classes": []},
                    {"name": "지혜의 목걸이", "magic_attack": 5, "durability": 160, "classes": []},
                    {"name": "체력의 반지", "hp": 20, "durability": 220, "classes": []},
                    {"name": "마나의 반지", "mp": 15, "durability": 190, "classes": []},
                    {"name": "방어의 목걸이", "defense": 4, "durability": 200, "classes": []},
                    {"name": "정확성의 반지", "accuracy": 10, "durability": 170, "classes": []},
                    {"name": "회피의 목걸이", "evasion": 8, "durability": 160, "classes": []},
                    {"name": "균형의 목걸이", "all_stats": 2, "durability": 150, "classes": []},
                    {"name": "용기의 반지", "bravery": 10, "durability": 180, "classes": []}
                ],
                "고급": [
                    {"name": "전설의 반지", "attack": 8, "defense": 5, "durability": 300, "special": "모든 능력치 +3", "classes": []},
                    {"name": "그림자 목걸이", "speed": 12, "evasion": 15, "durability": 250, "special": "크리티컬 회피 +10%", "classes": []},
                    {"name": "대마법사 반지", "magic_attack": 12, "mp": 25, "durability": 280, "special": "마법 크리티컬 +8%", "classes": []},
                    {"name": "성스러운 목걸이", "defense": 10, "magic_defense": 8, "durability": 320, "special": "회복 효과 +20%", "classes": []},
                    {"name": "용의 심장", "hp": 50, "attack": 6, "durability": 350, "special": "화염 저항 +30%", "classes": []},
                    {"name": "시간의 목걸이", "speed": 15, "magic_attack": 8, "durability": 260, "special": "행동 속도 +10%", "classes": []}
                ]
            },
            "소비품": {
                "일반": [
                    {"name": "체력 포션", "effect": "HP 회복", "value": 50, "quantity": 3},
                    {"name": "마나 포션", "effect": "MP 회복", "value": 30, "quantity": 3},
                    {"name": "해독제", "effect": "독 치료", "value": 1, "quantity": 2},
                    {"name": "힘의 물약", "effect": "공격력 증가", "value": 10, "duration": 5, "quantity": 2},
                    {"name": "민첩 물약", "effect": "속도 증가", "value": 8, "duration": 5, "quantity": 2},
                    {"name": "방어 물약", "effect": "방어력 증가", "value": 8, "duration": 5, "quantity": 2},
                    {"name": "집중 물약", "effect": "명중률 증가", "value": 15, "duration": 5, "quantity": 2},
                    {"name": "회복 허브", "effect": "지속 회복", "value": 10, "duration": 3, "quantity": 2},
                    {"name": "에너지 드링크", "effect": "피로 회복", "value": 1, "quantity": 2},
                    {"name": "마법 가루", "effect": "마법 저항", "value": 20, "duration": 3, "quantity": 1}
                ],
                "고급": [
                    {"name": "상급 체력 포션", "effect": "HP 대량 회복", "value": 100, "quantity": 2},
                    {"name": "상급 마나 포션", "effect": "MP 대량 회복", "value": 60, "quantity": 2},
                    {"name": "만능 해독제", "effect": "모든 상태이상 치료", "value": 1, "quantity": 1},
                    {"name": "전투 자극제", "effect": "모든 능력치 증가", "value": 15, "duration": 8, "quantity": 1},
                    {"name": "재생 물약", "effect": "강력한 지속 회복", "value": 20, "duration": 5, "quantity": 1},
                    {"name": "마법 증폭제", "effect": "마법 위력 증가", "value": 25, "duration": 6, "quantity": 1},
                    {"name": "불사의 물약", "effect": "일시적 무적", "value": 1, "duration": 2, "quantity": 1},
                    {"name": "시간 가속 물약", "effect": "행동 속도 대폭 증가", "value": 30, "duration": 4, "quantity": 1}
                ]
            }
        }
    
    def _init_class_preferences(self) -> Dict[str, Dict[str, List[str]]]:
        """직업별 선호 아이템 타입 정의"""
        return {
            "전사": {"weapon": ["검", "도끼"], "armor": ["중갑"], "accessory": ["힘", "체력"]},
            "아크메이지": {"weapon": ["지팡이"], "armor": ["로브"], "accessory": ["지혜", "마나"]},
            "궁수": {"weapon": ["활"], "armor": ["경갑"], "accessory": ["민첩", "정확성"]},
            "도적": {"weapon": ["단검"], "armor": ["경갑"], "accessory": ["민첩", "회피"]},
            "성기사": {"weapon": ["검", "메이스"], "armor": ["중갑"], "accessory": ["체력", "방어"]},
            "암흑기사": {"weapon": ["검"], "armor": ["중갑"], "accessory": ["힘", "체력"]},
            "몽크": {"weapon": ["장갑"], "armor": ["수도복"], "accessory": ["민첩", "회피"]},
            "바드": {"weapon": ["하프"], "armor": ["경갑"], "accessory": ["균형"]},
            "네크로맨서": {"weapon": ["지팡이"], "armor": ["로브"], "accessory": ["지혜", "마나"]},
            "용기사": {"weapon": ["검"], "armor": ["용린갑옷"], "accessory": ["용기", "체력"]},
            "검성": {"weapon": ["검"], "armor": ["도복"], "accessory": ["힘", "민첩"]},
            "정령술사": {"weapon": ["지팡이"], "armor": ["로브"], "accessory": ["지혜", "마나"]},
            "시간술사": {"weapon": ["지팡이"], "armor": ["로브"], "accessory": ["시간", "마나"]},
            "연금술사": {"weapon": ["지팡이"], "armor": ["로브"], "accessory": ["지혜", "마나"]},
            "차원술사": {"weapon": ["지팡이"], "armor": ["로브"], "accessory": ["지혜", "마나"]},
            "마검사": {"weapon": ["검"], "armor": ["중갑"], "accessory": ["힘", "마나"]},
            "기계공학자": {"weapon": ["레이저건"], "armor": ["기계슈트"], "accessory": ["정확성", "체력"]},
            "무당": {"weapon": ["지팡이"], "armor": ["의복"], "accessory": ["지혜", "마나"]},
            "암살자": {"weapon": ["단검"], "armor": ["경갑"], "accessory": ["민첩", "회피"]},
            "해적": {"weapon": ["검", "활"], "armor": ["경갑"], "accessory": ["민첩", "힘"]},
            "사무라이": {"weapon": ["도"], "armor": ["도복"], "accessory": ["용기", "힘"]},
            "드루이드": {"weapon": ["지팡이"], "armor": ["자연갑옷"], "accessory": ["균형", "지혜"]},
            "철학자": {"weapon": ["철학서"], "armor": ["로브"], "accessory": ["지혜", "마나"]},
            "검투사": {"weapon": ["검"], "armor": ["중갑"], "accessory": ["힘", "체력"]},
            "기사": {"weapon": ["창", "검"], "armor": ["중갑"], "accessory": ["체력", "방어"]},
            "신관": {"weapon": ["메이스"], "armor": ["성직자의복"], "accessory": ["방어", "마나"]},
            "광전사": {"weapon": ["도끼", "검"], "armor": ["중갑"], "accessory": ["힘", "체력"]}
        }
    
    def generate_starting_items(self, character_class: str, level: int = 1) -> Dict[str, List[Dict]]:
        """직업과 레벨에 맞는 시작 아이템 생성 - 캐릭터당 2개 장비 보장"""
        items = {
            "equipment": [],  # 장비 2개 (무기/방어구 우선, 장신구는 1개 슬롯 비워둠)
            "consumables": []  # 소비 아이템 2개
        }
        
        # 아이템 등급 결정 (일반 70%, 고급 30%)
        grade = "고급" if random.random() < 0.3 else "일반"
        
        # 장비 2종 확정 지급 (무기 + 방어구를 우선으로, 때로는 장신구 포함)
        # 무기와 방어구를 우선 제공하되, 가끔 장신구도 포함
        equipment_types = ["무기", "방어구", "장신구"]
        
        # 80% 확률로 무기+방어구, 20% 확률로 다른 조합
        if random.random() < 0.8:
            selected_equipment_types = ["무기", "방어구"]
        else:
            # 다양성을 위해 가끔 다른 조합도 제공
            selected_equipment_types = random.sample(equipment_types, 2)
        
        # 각 선택된 장비 타입에 대해 아이템 생성
        for eq_type in selected_equipment_types:
            suitable_items = self._get_suitable_items(eq_type, character_class, grade)
            if suitable_items:
                selected_item = random.choice(suitable_items)
                # 레벨에 따른 스탯 보정
                adjusted_item = self._adjust_item_for_level(selected_item.copy(), level)
                items["equipment"].append(adjusted_item)
        
        # 만약 장비가 2개 미만이면 추가 장비 제공 (보험)
        while len(items["equipment"]) < 2:
            remaining_types = [t for t in equipment_types if not any(item.get("type") == t for item in items["equipment"])]
            if remaining_types:
                eq_type = random.choice(remaining_types)
                suitable_items = self._get_suitable_items(eq_type, character_class, grade)
                if suitable_items:
                    selected_item = random.choice(suitable_items)
                    adjusted_item = self._adjust_item_for_level(selected_item.copy(), level)
                    items["equipment"].append(adjusted_item)
            else:
                break
        
        # 소비 아이템 2개 선택
        consumable_items = self.item_database["소비품"][grade]
        selected_consumables = random.sample(consumable_items, min(2, len(consumable_items)))
        
        for consumable in selected_consumables:
            items["consumables"].append(consumable.copy())
        
        return items
    
    def _get_suitable_items(self, item_type: str, character_class: str, grade: str) -> List[Dict]:
        """직업에 적합한 아이템 목록 반환"""
        if item_type not in self.item_database:
            return []
        
        if grade not in self.item_database[item_type]:
            return []
        
        suitable_items = []
        for item in self.item_database[item_type][grade]:
            if "classes" in item and character_class in item["classes"]:
                suitable_items.append(item)
        
        # 적합한 아이템이 없으면 모든 아이템에서 선택
        if not suitable_items:
            suitable_items = self.item_database[item_type][grade]
        
        return suitable_items
    
    def _adjust_item_for_level(self, item: Dict, level: int) -> Dict:
        """스타팅 아이템은 레벨에 따른 스탯 조정을 하지 않음 (일회용 장비)"""
        # 스타팅 아이템은 성장하지 않음 - 그대로 반환
        return item
    
    def get_item_description(self, item: Dict) -> str:
        """아이템 설명 생성"""
        desc_parts = [item["name"]]
        
        # 스탯 정보
        stats = []
        if "attack" in item:
            stats.append(f"공격력 +{item['attack']}")
        if "defense" in item:
            stats.append(f"방어력 +{item['defense']}")
        if "magic_attack" in item:
            stats.append(f"마법공격 +{item['magic_attack']}")
        if "magic_defense" in item:
            stats.append(f"마법방어 +{item['magic_defense']}")
        if "hp" in item:
            stats.append(f"체력 +{item['hp']}")
        if "mp" in item:
            stats.append(f"마나 +{item['mp']}")
        if "speed" in item:
            stats.append(f"속도 +{item['speed']}")
        
        if stats:
            desc_parts.append(f"({', '.join(stats)})")
        
        # 특수 효과
        if "special" in item:
            desc_parts.append(f"[{item['special']}]")
        
        # 내구도
        if "durability" in item:
            desc_parts.append(f"내구도: {item['durability']}")
        
        return " ".join(desc_parts)
    
    def create_item_for_inventory(self, item_data: Dict) -> Dict:
        """인벤토리용 아이템 객체 생성"""
        inventory_item = {
            "name": item_data["name"],
            "type": self._determine_item_type(item_data),
            "description": self.get_item_description(item_data),
            "stats": self._extract_stats(item_data),
            "durability": item_data.get("durability", 100),
            "max_durability": item_data.get("durability", 100),
            "special_effects": item_data.get("special", ""),
            "grade": "고급" if "special" in item_data else "일반",
            "weight": 0,  # 스타팅 아이템은 무게 0kg
            "sell_price": 0,  # 스타팅 아이템은 판매 불가
            "is_starting_item": True  # 스타팅 아이템 표시
        }
        
        # 소비품의 경우 수량 정보 추가
        if "quantity" in item_data:
            inventory_item["quantity"] = item_data["quantity"]
            inventory_item["effect"] = item_data.get("effect", "")
            inventory_item["value"] = item_data.get("value", 0)
        
        return inventory_item
    
    def _determine_item_type(self, item_data: Dict) -> str:
        """아이템 데이터로부터 타입 결정"""
        if "effect" in item_data:
            return "소비품"
        elif "attack" in item_data or "magic_attack" in item_data:
            return "무기"
        elif "defense" in item_data or "magic_defense" in item_data:
            return "방어구"
        else:
            return "장신구"
    
    def _extract_stats(self, item_data: Dict) -> Dict:
        """아이템 데이터에서 스탯 추출"""
        stats = {}
        stat_keys = ["attack", "defense", "magic_attack", "magic_defense", 
                    "hp", "mp", "speed", "accuracy", "evasion", "bravery"]
        
        for key in stat_keys:
            if key in item_data:
                stats[key] = item_data[key]
        
        return stats

# 전역 인스턴스
enhanced_items = EnhancedStartingItems()

# 편의 함수
def generate_starting_items_for_class(character_class: str, level: int = 1) -> Dict[str, List[Dict]]:
    """직업별 시작 아이템 생성"""
    return enhanced_items.generate_starting_items(character_class, level)

def get_item_description(item: Dict) -> str:
    """아이템 설명 반환"""
    return enhanced_items.get_item_description(item)

def create_inventory_item(item_data: Dict) -> Dict:
    """인벤토리용 아이템 생성"""
    return enhanced_items.create_item_for_inventory(item_data)