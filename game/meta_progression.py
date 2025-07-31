"""
메타 진행 시스템 - 게임 오버 후 보상 및 해금 시스템
영구적 성장을 통한 점진적 강화
"""

import json
import os
from typing import Dict, List


class MetaProgression:
    """메타 진행 관리 클래스"""
    
    def __init__(self, save_file: str = "meta_progress.json"):
        self.save_file = save_file
        self.data = self.load_data()
        
    def load_data(self) -> Dict:
        """저장된 진행 데이터 로드"""
        default_data = {
            "total_runs": 0,
            "best_score": 0,
            "total_floors_cleared": 0,
            "total_enemies_defeated": 0,
            "total_items_collected": 0,
            "unlocked_classes": ["전사", "아크메이지", "궁수", "도적"],  # 시작 직업들 (4개)
            "star_fragments": 0,  # 별조각 (메타 재화)
            
            # 영구적 업그레이드
            "permanent_upgrades": {
                "hp_bonus": 0,           # HP 증가 (1당 +5%)
                "attack_bonus": 0,       # 공격력 증가 (1당 +3%)
                "defense_bonus": 0,      # 방어력 증가 (1당 +3%)
                "speed_bonus": 0,        # 속도 증가 (1당 +2%)
                "exp_bonus": 0,          # 경험치 증가 (1당 +10%)
                "item_find_bonus": 0,    # 아이템 발견률 (1당 +5%)
                "gold_bonus": 0,         # 골드 획득량 (1당 +10%)
                "passive_unlock": 0,     # 패시브 해금 속도 (1당 추가 패시브 1개)
                "starting_level": 0,     # 시작 레벨 (1당 +1레벨)
                "healing_bonus": 0       # 회복 효과 증가 (1당 +15%)
            },
            
            # 직업별 숙련도
            "class_mastery": {},
            
            # 업적
            "achievements": [],
            
            # 통계
            "statistics": {
                "longest_run": 0,
                "total_deaths": 0,
                "favorite_class": "전사",
                "most_killed_enemy": "고블린"
            }
        }
        
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    # 기본 데이터로 누락된 키들 채우기
                    for key, value in default_data.items():
                        if key not in loaded_data:
                            loaded_data[key] = value
                    return loaded_data
            except:
                return default_data
        return default_data
    def save_data(self):
        """진행 데이터 저장"""
        try:
            with open(self.save_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"저장 실패: {e}")
    
    def get_upgrade_cost(self, upgrade_type: str) -> int:
        """업그레이드 비용 계산"""
        current_level = self.data["permanent_upgrades"].get(upgrade_type, 0)
        base_costs = {
            "hp_bonus": 50,
            "attack_bonus": 75,
            "defense_bonus": 75,
            "speed_bonus": 60,
            "exp_bonus": 100,
            "item_find_bonus": 80,
            "gold_bonus": 90,
            "passive_unlock": 150,
            "starting_level": 200,
            "healing_bonus": 120
        }
        base_cost = base_costs.get(upgrade_type, 50)
        # 레벨당 20% 증가
        return int(base_cost * (1.2 ** current_level))
    
    def can_afford_upgrade(self, upgrade_type: str) -> bool:
        """업그레이드 구매 가능 여부"""
        cost = self.get_upgrade_cost(upgrade_type)
        return self.data["star_fragments"] >= cost
    
    def purchase_upgrade(self, upgrade_type: str) -> bool:
        """업그레이드 구매"""
        if not self.can_afford_upgrade(upgrade_type):
            return False
        
        cost = self.get_upgrade_cost(upgrade_type)
        self.data["star_fragments"] -= cost
        self.data["permanent_upgrades"][upgrade_type] += 1
        self.save_data()
        return True
    
    def get_upgrade_description(self, upgrade_type: str) -> str:
        """업그레이드 설명"""
        descriptions = {
            "hp_bonus": "모든 캐릭터의 최대 HP +5%",
            "attack_bonus": "모든 캐릭터의 공격력 +3%",
            "defense_bonus": "모든 캐릭터의 방어력 +3%",
            "speed_bonus": "모든 캐릭터의 속도 +2%",
            "exp_bonus": "경험치 획득량 +10%",
            "item_find_bonus": "아이템 발견 확률 +5%",
            "gold_bonus": "골드 획득량 +10%",
            "passive_unlock": "시작 시 추가 패시브 1개 해금",
            "starting_level": "시작 레벨 +1",
            "healing_bonus": "모든 회복 효과 +15%"
        }
        return descriptions.get(upgrade_type, "알 수 없는 업그레이드")
            
    def record_game_end(self, score: int, enemies_defeated: int, items_collected: int, 
                       floors_cleared: int, victory: bool = False):
        """게임 종료 시 결과 기록"""
        self.data["total_runs"] += 1
        self.data["total_floors_cleared"] = max(self.data["total_floors_cleared"], floors_cleared)
        self.data["total_enemies_defeated"] += enemies_defeated
        self.data["total_items_collected"] += items_collected
        
        if score > self.data["best_score"]:
            self.data["best_score"] = score
            
        # 보상 계산
        rewards = self.calculate_rewards(score, enemies_defeated, items_collected, floors_cleared, victory)
        self.apply_rewards(rewards)
        
        # 업적 체크
        self.check_achievements()
        
        self.save_data()
        return rewards
        
    def calculate_rewards(self, score: int, enemies_defeated: int, items_collected: int,
                         floors_cleared: int, victory: bool) -> Dict:
        """보상 계산"""
        rewards = {
            "star_fragments": 0,
            "unlocked_classes": [],
            "achievements": []
        }
        
        # 기본 별조각 보상
        base_fragments = floors_cleared * 10 + enemies_defeated * 2 + items_collected
        if victory:
            base_fragments *= 2
            
        # 연속 실패 보상 (어려움 보정)
        if self.data["total_runs"] > 0:
            recent_runs_bonus = min(self.data["total_runs"] * 2, 50)
            base_fragments += recent_runs_bonus
            
        rewards["star_fragments"] = base_fragments
        self.data["star_fragments"] += base_fragments
        
        # 직업 해금 조건 체크
        all_classes = [
            "전사", "아크메이지", "궁수", "도적", "성기사", "암흑기사", "몽크",
            "바드", "네크로맨서", "용기사", "검성", "정령술사", "암살자", "기계공학자",
            "무당", "해적", "사무라이", "드루이드", "철학자", "시간술사", "연금술사",
            "검투사", "기사", "신관", "마검사", "차원술사", "광전사"
        ]
        
        for class_name in all_classes:
            if class_name not in self.data["unlocked_classes"]:
                if self.check_class_unlock_condition(class_name):
                    self.data["unlocked_classes"].append(class_name)
                    rewards["unlocked_classes"].append(class_name)
                    
        return rewards
        
    def check_class_unlock_condition(self, class_name: str) -> bool:
        """직업 해금 조건 확인"""
        unlock_conditions = {
            # 기본 4개는 이미 해금됨
            "성기사": {"total_runs": 2},
            "암흑기사": {"total_enemies_defeated": 15},
            "몽크": {"total_runs": 3},
            "바드": {"total_items_collected": 10},
            "네크로맨서": {"best_score": 500},
            "용기사": {"total_runs": 5},
            "검성": {"total_enemies_defeated": 30},
            "정령술사": {"total_runs": 4},
            "암살자": {"best_score": 750},
            "기계공학자": {"total_items_collected": 20},
            "무당": {"total_runs": 6},
            "해적": {"total_enemies_defeated": 50},
            "사무라이": {"best_score": 1000},
            "드루이드": {"total_runs": 8},
            "철학자": {"total_items_collected": 30},
            "시간술사": {"best_score": 1500},
            "연금술사": {"total_runs": 10},
            "검투사": {"total_enemies_defeated": 75},
            "기사": {"best_score": 2000},
            "신관": {"total_runs": 12},
            "마검사": {"total_items_collected": 40},
            "차원술사": {"best_score": 2500},
            "광전사": {"total_enemies_defeated": 100}
        }
        
        condition = unlock_conditions.get(class_name)
        if not condition:
            return False
            
        for req_type, req_value in condition.items():
            if self.data.get(req_type, 0) < req_value:
                return False
        return True
    
    def apply_bonuses_to_character(self, character):
        """캐릭터에 영구 업그레이드 보너스 적용"""
        upgrades = self.data["permanent_upgrades"]
        
        # HP 보너스
        hp_bonus = 1 + (upgrades.get("hp_bonus", 0) * 0.05)
        character.max_hp = int(character.max_hp * hp_bonus)
        character.current_hp = character.max_hp
        
        # 공격력 보너스
        attack_bonus = 1 + (upgrades.get("attack_bonus", 0) * 0.03)
        character.physical_attack = int(character.physical_attack * attack_bonus)
        character.magic_attack = int(character.magic_attack * attack_bonus)
        
        # 방어력 보너스
        defense_bonus = 1 + (upgrades.get("defense_bonus", 0) * 0.03)
        character.physical_defense = int(character.physical_defense * defense_bonus)
        character.magic_defense = int(character.magic_defense * defense_bonus)
        
        # 속도 보너스
        speed_bonus = 1 + (upgrades.get("speed_bonus", 0) * 0.02)
        character.speed = int(character.speed * speed_bonus)
        
        # 시작 레벨 보너스
        starting_level_bonus = upgrades.get("starting_level", 0)
        if starting_level_bonus > 0:
            for _ in range(starting_level_bonus):
                character.level += 1
                gains = character.calculate_level_up_gains()
                character.apply_level_up_gains(gains)
        
        return character
    
    def check_achievements(self):
        """업적 체크"""
        achievements = [
            {"name": "첫 모험", "condition": "total_runs", "value": 1, "reward": 50},
            {"name": "베테랑 모험가", "condition": "total_runs", "value": 10, "reward": 100},
            {"name": "몬스터 헌터", "condition": "total_enemies_defeated", "value": 100, "reward": 150},
            {"name": "보물 사냥꾼", "condition": "total_items_collected", "value": 50, "reward": 100},
            {"name": "점수 마스터", "condition": "best_score", "value": 2000, "reward": 200}
        ]
        
        for achievement in achievements:
            if (achievement["name"] not in self.data["achievements"] and
                self.data.get(achievement["condition"], 0) >= achievement["value"]):
                
                self.data["achievements"].append(achievement["name"])
                self.data["star_fragments"] += achievement["reward"]
    
    def get_unlocked_characters(self) -> List[str]:
        """해금된 캐릭터 목록 반환"""
        return self.data.get("unlocked_classes", ["전사", "아크메이지", "궁수", "도적"])
        
    def get_persistent_items(self) -> List[str]:
        """지속 아이템 목록 반환"""
        return self.data.get("persistent_items", [])
        
    def use_persistent_item(self, item_name: str) -> bool:
        """지속 아이템 사용"""
        items = self.data.get("persistent_items", [])
        if item_name in items:
            items.remove(item_name)
            self.save_data()
            return True
        return False
        
    def upgrade_character(self, char_name: str) -> bool:
        """캐릭터 업그레이드"""
        if "character_upgrades" not in self.data:
            self.data["character_upgrades"] = {}
        
        current_level = self.data["character_upgrades"].get(char_name, 0)
        cost = 100 * (current_level + 1)
        
        if self.data.get("star_fragments", 0) >= cost:
            self.data["star_fragments"] -= cost
            self.data["character_upgrades"][char_name] = current_level + 1
            self.save_data()
            return True
        return False
        
    def get_character_upgrade_level(self, char_name: str) -> int:
        """캐릭터 업그레이드 레벨 반환"""
        return self.data.get("character_upgrades", {}).get(char_name, 0)
        
    def show_unlock_progress(self):
        """해금 진행상황 표시"""
        print("\n=== 캐릭터 해금 진행상황 ===")
        try:
            from .character_database import CharacterDatabase
            all_characters = CharacterDatabase.get_all_characters()
        except ImportError:
            print("캐릭터 데이터베이스를 불러올 수 없습니다.")
            return
            
        for char in all_characters:
            char_name = char["name"]
            if char_name in self.data.get("unlocked_classes", []):
                print(f"✓ {char_name} - 해금됨")
            else:
                print(f"✗ {char_name} - 해금 조건을 만족하지 않음")
                
    def reset_progress(self):
        """진행도 초기화 (개발/테스트용)"""
        if os.path.exists(self.save_file):
            os.remove(self.save_file)
        self.data = self.load_data()
    
    def update_floors_cleared(self, floors: int):
        """클리어한 층수 업데이트"""
        if "floors_cleared" not in self.data:
            self.data["floors_cleared"] = 0
        if floors > self.data["floors_cleared"]:
            self.data["floors_cleared"] = floors
        self.save_data()

# 전역 메타 진행 시스템
meta_progression = MetaProgression()

def get_meta_progression() -> MetaProgression:
    """메타 진행 시스템 반환"""
    return meta_progression
